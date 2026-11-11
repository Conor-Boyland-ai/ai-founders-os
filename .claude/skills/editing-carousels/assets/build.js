#!/usr/bin/env node
/*
 * build.js — render a carousel from a slides data file.
 *
 *   node assets/build.js slides.js "My Carousel.dc.html"
 *
 * The input file is a CommonJS module that exports the slides list and options:
 *
 *   // slides.js
 *   module.exports = {
 *     theme: 'dark',                   // 'dark' (black bg/white text) | 'light' (white bg/black text)
 *     align: 'center',                 // 'center' (default) | 'left' — one per carousel
 *     slides: [
 *       { text: 'The question {_isn’t_} whether your strategy can make money.' },
 *       { text: 'Comment WRITE and I’ll send it.', keyword: 'WRITE' },
 *       // …in script order
 *     ],
 *   };
 *
 * Output is a complete .dc.html. Keep support.js, deck-stage.js, and
 * image-slot.js beside the output file so it renders.
 */
const fs = require('fs');
const path = require('path');
const K = require('./carousel-kit.js');

const input = process.argv[2];
const out = process.argv[3] || 'carousel.dc.html';
if (!input) {
  console.error('Usage: node assets/build.js <slides.js> [output.dc.html]');
  process.exit(1);
}

const mod = require(path.resolve(input));
const slides = Array.isArray(mod) ? mod : mod.slides;
const theme = mod && mod.theme;

// Cover framing set by the user on the batch review page (apply-framing.py writes cover-render.json
// next to the deck files). Merged into the cover slide: title nudge, size, alignment.
const renderPath = path.join(path.dirname(path.resolve(input)), 'cover-render.json');
const deckNum = (path.basename(input).match(/^c(\d+)-/) || [])[1];
if (deckNum && fs.existsSync(renderPath)) {
  const f = JSON.parse(fs.readFileSync(renderPath, 'utf8'))[String(+deckNum)];
  if (f && slides[0]) Object.assign(slides[0], f);
}

if (!Array.isArray(slides) || !slides.length) {
  console.error('No slides found. Export { slides: [...] } or an array.');
  process.exit(1);
}

if (theme !== 'dark' && theme !== 'light') {
  console.error('Set `theme: \'dark\'` or `theme: \'light\'` in ' + input + ' — one theme per carousel, no default.');
  process.exit(1);
}

// No slide cap (the user, 2026-09-07): 1 bullet = 1 slide. Never condense.
if (slides.length > 10) console.warn('  Note: ' + slides.length + ' slides. Over Instagram\'s documented API cap of 10 — render anyway, tell the user.');

// Guards for the flat-text kit: every slide needs lines; a slide with 5+
// paragraphs is probably two slides.
slides.forEach(function (s, i) {
  var n = 'Slide ' + (i + 1);
  var t = s.text != null ? s.text : (s.headline || (s.lines || []).join(' '));
  if (!t.trim()) console.warn('  ' + n + ': slide with no `text`.');
});

fs.writeFileSync(out, K.buildCarouselHTML(slides, { theme: theme, align: mod.align, top: mod.top, maxH: mod.maxH, width: mod.width, quoteW: mod.quoteW, bottom: mod.bottom, backdrop: mod.backdrop, plain: mod.plain, accent: mod.accent }));
console.log('Wrote ' + out + '  (' + slides.length + ' slides)');
