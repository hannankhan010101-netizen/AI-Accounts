/** Inline script to apply theme before paint (avoids flash). */
export function ThemeScript() {
  const script = `
(function() {
  try {
    var mode = localStorage.getItem('theme:mode');
    var dark = mode === 'dark' || (mode !== 'light' && window.matchMedia('(prefers-color-scheme: dark)').matches);
    document.documentElement.classList.add(dark ? 'dark' : 'light');
  } catch (e) {}
})();
`;
  return <script dangerouslySetInnerHTML={{ __html: script }} />;
}
