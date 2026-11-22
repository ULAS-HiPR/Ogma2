# Fonts for Burrito's silkscreen

`texgyreheros-bold.otf` is TeX Gyre Heros Bold 2.004, a free Helvetica-style typeface by Bogusław Jackowski and
Janusz M. Nowacki (GUST e-foundry), copied unchanged from Ubuntu's `fonts-texgyre` 20180621-6.

- Copyright © 2007–2018 Bogusław Jackowski and Janusz M. Nowacki.
- Licence: the GUST Font License, which is the LaTeX Project Public License 1.3c or later with a request, not
  a requirement, to rename modified fonts: <http://www.gust.org.pl/fonts/licenses/GUST-FONT-LICENSE.txt>.
- Source: <http://www.gust.org.pl/projects/e-foundry/tex-gyre/heros>.

`tools/layout/engine/art.py` reads the outlines with fontTools and draws the word BURRITO as polygons, so the
board file holds shapes, not a font name, and looks the same on any machine (D-22Nov.12).
