// Composes store images from raw app screenshots. Config driven; knows nothing
// about any one app.
//
//   STORE_JOBS=/abs/path/jobs.json flutter test test/compose_test.dart
//
// jobs.json
//   { "fonts": [ { "family": "Brand", "files": ["/abs/Brand-Bold.ttf"] } ],
//     "jobs": [
//       { "type": "framed", "raw": "/abs/raw.png", "caption": "Headline", "out": "/abs/out.png",
//         "canvas": [1080, 1920], "style": { ... } },
//       { "type": "icon", "src": "/abs/art.png", "srcRect": [x, y, w, h],   // part of the art to keep
//         "bgAt": [x, y],            // pixel in the art whose colour becomes the flat background
//         "fade": 0.62,              // how far the art stays opaque before fading to the flat colour (default 0.62)
//         "inset": 0.10,             // margin around the art, as a fraction of the icon (default 0.10)
//         "canvas": [1024, 1024], "out": "/abs/icon-1024.png" },
//       { "type": "feature", "icon": "/abs/icon.png", "raw": "/abs/raw.png",
//         "name": "App", "tagline": "What it does", "out": "/abs/fg.png", "canvas": [1024, 500],
//         "style": { ... } } ] }
//
// style (all optional)
//   bg        list of 2-3 hex colours for the diagonal gradient
//   text      caption colour      accent  tagline / highlight colour
//   bezel     device bezel colour
//   font      caption font family (default Roboto, from the Flutter SDK)
//   weight    caption weight 100..900 (default 800)
//   scale     caption size multiplier (default 1.0)
//   device    phone | tablet | desktop  (corner radius and bezel thickness)
//   align     left | center (caption alignment, default left)
//
// Output is RGB PNG (no alpha): both stores reject screenshots with an alpha channel.
import 'dart:convert';
import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as img;

final _jobsPath = Platform.environment['STORE_JOBS'];

Color _hex(String s) {
  final h = s.replaceFirst('#', '');
  return Color(int.parse(h.length == 6 ? 'FF$h' : h, radix: 16));
}

Future<void> _loadFonts(List<dynamic> custom) async {
  ByteData bytes(String p) => ByteData.view(File(p).readAsBytesSync().buffer);
  for (final f in custom) {
    final loader = FontLoader(f['family'] as String);
    for (final file in (f['files'] as List)) {
      loader.addFont(Future.value(bytes(file as String)));
    }
    await loader.load();
  }
  // Real Roboto from the SDK, for the default caption font.
  final sdk = '${Platform.environment['FLUTTER_ROOT'] ?? ''}/bin/cache/artifacts/material_fonts';
  if (Directory(sdk).existsSync()) {
    final loader = FontLoader('Roboto');
    for (final w in ['Regular', 'Medium', 'Bold', 'Black', 'Light']) {
      final f = File('$sdk/Roboto-$w.ttf');
      if (f.existsSync()) loader.addFont(Future.value(bytes(f.path)));
    }
    await loader.load();
  }
}

class _Style {
  _Style(Map<String, dynamic>? j)
      : bg = ((j?['bg'] as List?) ?? ['#0B3D2E', '#115740']).map((e) => _hex(e as String)).toList(),
        text = _hex((j?['text'] as String?) ?? '#FFFFFF'),
        accent = _hex((j?['accent'] as String?) ?? '#FFD166'),
        bezel = _hex((j?['bezel'] as String?) ?? '#14110F'),
        font = (j?['font'] as String?) ?? 'Roboto',
        weight = (j?['weight'] as num?)?.toInt() ?? 800,
        scale = (j?['scale'] as num?)?.toDouble() ?? 1.0,
        device = (j?['device'] as String?) ?? 'phone',
        center = (j?['align'] as String?) == 'center';

  final List<Color> bg;
  final Color text, accent, bezel;
  final String font, device;
  final int weight;
  final double scale;
  final bool center;

  double get radius => switch (device) {
        'tablet' => 0.035,
        'desktop' => 0.012,
        _ => 0.068,
      };

  FontWeight get fontWeight => FontWeight.values[((weight ~/ 100) - 1).clamp(0, 8)];

  BoxDecoration get background => BoxDecoration(
        gradient: LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: bg.length == 1 ? [bg[0], bg[0]] : bg),
      );
}

Future<ui.Image> _decode(WidgetTester t, String path) async {
  late ui.Image image;
  await t.runAsync(() async {
    final codec = await ui.instantiateImageCodec(File(path).readAsBytesSync());
    image = (await codec.getNextFrame()).image;
  });
  return image;
}

Future<void> _savePng(WidgetTester t, GlobalKey key, String path) async {
  await t.runAsync(() async {
    final boundary = key.currentContext!.findRenderObject() as RenderRepaintBoundary;
    final image = await boundary.toImage(pixelRatio: 1);
    final data = await image.toByteData(format: ui.ImageByteFormat.rawRgba);
    final rgb = img.Image.fromBytes(width: image.width, height: image.height, bytes: data!.buffer, numChannels: 4).convert(numChannels: 3);
    File(path)
      ..createSync(recursive: true)
      ..writeAsBytesSync(img.encodePng(rgb));
  });
}

Widget _framed(ui.Image screen, String caption, Size canvas, _Style st) {
  final w = canvas.width, h = canvas.height;
  final base = w < h ? w : h;
  final bezel = base * (st.device == 'phone' ? 0.014 : 0.012);
  final capH = h * 0.19;
  final top = capH + h * 0.015;
  final avail = h - top - h * 0.03;
  final ratio = screen.height / screen.width;
  final deviceW = (avail / ratio + 2 * bezel).clamp(0.0, w * 0.86);
  final screenW = deviceW - 2 * bezel;
  final screenH = screenW * ratio;
  final r = base * st.radius;
  return Container(
    decoration: st.background,
    child: Stack(children: [
      Positioned(
        right: -base * 0.18,
        top: -base * 0.18,
        child: Container(width: base * 0.62, height: base * 0.62, decoration: BoxDecoration(shape: BoxShape.circle, color: st.accent.withValues(alpha: 0.12))),
      ),
      Positioned(
        left: w * 0.07,
        right: w * 0.07,
        top: h * 0.035,
        height: capH - h * 0.035,
        child: Align(
          alignment: st.center ? Alignment.center : Alignment.centerLeft,
          child: Text(
            caption,
            maxLines: 3,
            textAlign: st.center ? TextAlign.center : TextAlign.start,
            style: TextStyle(fontFamily: st.font, fontWeight: st.fontWeight, fontSize: base * 0.072 * st.scale, height: 1.15, color: st.text),
          ),
        ),
      ),
      Positioned(
        top: top,
        left: (w - deviceW) / 2,
        width: deviceW,
        child: Container(
          padding: EdgeInsets.all(bezel),
          decoration: BoxDecoration(
            color: st.bezel,
            borderRadius: BorderRadius.circular(r + bezel),
            boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.35), blurRadius: base * 0.04, offset: Offset(0, base * 0.015))],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(r),
            child: SizedBox(width: screenW, height: screenH, child: RawImage(image: screen, fit: BoxFit.fill, filterQuality: FilterQuality.high)),
          ),
        ),
      ),
    ]),
  );
}

Widget _feature(ui.Image icon, ui.Image screen, String name, String tagline, Size canvas, _Style st) {
  final w = canvas.width, h = canvas.height;
  final ratio = screen.height / screen.width;
  final devW = (w * 0.27).clamp(0.0, 360.0);
  return Container(
    decoration: st.background,
    child: Stack(children: [
      Positioned(right: -h * 0.24, top: -h * 0.32, child: Container(width: h * 0.96, height: h * 0.96, decoration: BoxDecoration(shape: BoxShape.circle, color: st.accent.withValues(alpha: 0.13)))),
      Positioned(
        left: w * 0.055,
        top: 0,
        bottom: 0,
        width: w * 0.55,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ClipRRect(borderRadius: BorderRadius.circular(h * 0.068), child: SizedBox(width: h * 0.24, height: h * 0.24, child: RawImage(image: icon, fit: BoxFit.fill, filterQuality: FilterQuality.high))),
            SizedBox(height: h * 0.044),
            Text(name, style: TextStyle(fontFamily: st.font, fontWeight: st.fontWeight, fontSize: h * 0.14 * st.scale, height: 1.1, color: st.text)),
            SizedBox(height: h * 0.016),
            Text(tagline, style: TextStyle(fontFamily: st.font, fontWeight: FontWeight.w500, fontSize: h * 0.062, height: 1.3, color: st.accent)),
          ],
        ),
      ),
      Positioned(
        right: w * 0.07,
        top: h * 0.104,
        width: devW,
        child: Container(
          padding: const EdgeInsets.all(5),
          decoration: BoxDecoration(color: st.bezel, borderRadius: BorderRadius.circular(36), boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.35), blurRadius: 24, offset: const Offset(0, 8))]),
          child: ClipRRect(borderRadius: BorderRadius.circular(31), child: SizedBox(width: devW - 10, height: (devW - 10) * ratio, child: RawImage(image: screen, fit: BoxFit.fill))),
        ),
      ),
    ]),
  );
}

class _IconPainter extends CustomPainter {
  _IconPainter(this.art, this.src, this.background, this.inset, this.fade);
  final ui.Image art;
  final Rect src;
  final Color background;
  final double inset;
  final double fade;

  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawRect(Offset.zero & size, Paint()..color = background);
    final side = size.width * (1 - 2 * inset);
    final dst = Rect.fromLTWH(size.width * inset, size.height * inset, side, side * src.height / src.width);
    // Fade the cropped square's edges into the flat colour, so no seam or corner shows.
    canvas.saveLayer(dst.inflate(2), Paint());
    canvas.drawImageRect(art, src, dst, Paint()..filterQuality = FilterQuality.high..isAntiAlias = true);
    canvas.drawRect(
      dst.inflate(2),
      Paint()
        ..blendMode = BlendMode.dstIn
        ..shader = ui.Gradient.radial(dst.center, dst.width * fade, const [Colors.white, Colors.white, Color(0x00FFFFFF)], const [0, 0.8, 1]),
    );
    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

void main() {
  testWidgets('compose store images', (t) async {
    final cfg = jsonDecode(File(_jobsPath!).readAsStringSync()) as Map<String, dynamic>;
    await t.runAsync(() => _loadFonts((cfg['fonts'] as List?) ?? const []));
    var n = 0;
    for (final job in (cfg['jobs'] as List).cast<Map<String, dynamic>>()) {
      final canvas = Size(((job['canvas'] as List)[0] as num).toDouble(), ((job['canvas'] as List)[1] as num).toDouble());
      final st = _Style(job['style'] as Map<String, dynamic>?);
      final raw = await _decode(t, (job['raw'] ?? job['src']) as String);
      Color? iconBg;
      if (job['type'] == 'icon') {
        final at = (job['bgAt'] as List).cast<num>();
        await t.runAsync(() async {
          final px = (await raw.toByteData())!;
          final i = (at[1].toInt() * raw.width + at[0].toInt()) * 4;
          iconBg = Color.fromARGB(255, px.getUint8(i), px.getUint8(i + 1), px.getUint8(i + 2));
        });
      }
      final Widget child = switch (job['type']) {
        'icon' => CustomPaint(
            painter: _IconPainter(raw, () {
              final r = (job['srcRect'] as List).cast<num>();
              return Rect.fromLTWH(r[0].toDouble(), r[1].toDouble(), r[2].toDouble(), r[3].toDouble());
            }(), iconBg!, (job['inset'] as num?)?.toDouble() ?? 0.10, (job['fade'] as num?)?.toDouble() ?? 0.62),
          ),
        'feature' => _feature(await _decode(t, job['icon'] as String), raw, job['name'] as String, job['tagline'] as String, canvas, st),
        _ => _framed(raw, job['caption'] as String, canvas, st),
      };
      t.view.physicalSize = canvas;
      t.view.devicePixelRatio = 1;
      final key = GlobalKey();
      await t.pumpWidget(Directionality(
        textDirection: TextDirection.ltr,
        child: RepaintBoundary(key: key, child: SizedBox.fromSize(size: canvas, child: child)),
      ));
      await t.pump(const Duration(milliseconds: 100));
      await _savePng(t, key, job['out'] as String);
      n++;
    }
    // ignore: avoid_print
    print('composed $n images');
  }, skip: _jobsPath == null);
}
