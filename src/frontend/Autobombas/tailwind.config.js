export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
    "./node_modules/@shadcn/ui/dist/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        itubombas: {
          verde: 'var(--color-itubombas-verde)',
          amarelo: 'var(--color-itubombas-amarelo)',
          verdeClaro: 'var(--color-itubombas-verde-claro)',
        }
      }
    },
  },
  plugins: [],
};
