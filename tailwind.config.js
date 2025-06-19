module.exports = {
  content: ["./templates/**/*.html"],
  theme: {
    extend: {
      transitionProperty: {
        opacity: 'opacity',
        transform: 'transform',
      },
    },
  },
  plugins: [require('daisyui').default],
};
