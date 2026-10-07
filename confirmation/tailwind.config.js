/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
    "./confirmation/**/*.py",   // classes écrites dans les vues/formulaires, le cas échéant
  ],
  theme: {
    extend: {
      colors: {
        una: {
          bg:   '#FBFAF6',
          band: '#EEF3EA',
          line: '#DCE3D6',
          ink:  '#17231B',
          mute: '#5C685F',
          mid:  '#2F7D4F',
          dark: '#0F3D2E',
          sun:  '#E9B44C',
          err:  '#B3392B',
        },
      },
      fontFamily: {
        display: ['Fraunces', 'Georgia', '"Times New Roman"', 'serif'],
      },
    },
  },
  plugins: [],
};
