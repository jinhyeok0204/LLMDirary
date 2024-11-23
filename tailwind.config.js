/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
    './templates/**/*.{html,js}',       // 최상위 templates 폴더의 HTML, JavaScript 파일
        './**/templates/**/*.{html,js}',
    './**/templates/**/*.{html,js}',    // 모든 앱 내부의 templates 폴더의 HTML, JavaScript 파일
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

