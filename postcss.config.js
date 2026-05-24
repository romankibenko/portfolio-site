// PostCSS используется при интеграции с bundler-ами (webpack, vite).
// Для сборки через npm run dev/build применяется @tailwindcss/cli напрямую —
// этот файл нужен для совместимости с инструментами, которые читают postcss.config.js.
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
  },
};
