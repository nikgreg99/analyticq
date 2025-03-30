import { useTheme } from "next-themes";

// Define custom colors
const colors = {
  brand: {
    50: '#e6f1ff',
    100: '#b3d7ff',
    200: '#80beff',
    300: '#4da5ff',
    400: '#1a8cff',
    500: '#0073e6',
    600: '#005ab3',
    700: '#004080',
    800: '#00264d',
    900: '#000d1a'
  },
  gray: {
    50: '#f5f7fa',
    100: '#e4e7eb',
    200: '#cbd2d9',
    300: '#9aa5b1',
    400: '#7b8794',
    500: '#616e7c',
    600: '#52606d',
    700: '#3e4c59',
    800: '#323f4b',
    900: '#1f2933'
  }
};

// Custom component styles
const components = {
  Button: {
    baseStyle: {
      fontWeight: 'bold',
      borderRadius: 'md'
    },
    variants: {
      solid: {
        bg: 'brand.500',
        color: 'white',
        _hover: {
          bg: 'brand.600'
        }
      }
    }
  },
  Input: {
    variants: {
      filled: {
        field: {
          bg: 'gray.100',
          _hover: {
            bg: 'gray.200'
          },
          _focus: {
            bg: 'white',
            borderColor: 'brand.500'
          }
        }
      }
    }
  },
  Radio: {
    baseStyle: {
      control: {
        _checked: {
          bg: 'brand.500',
          borderColor: 'brand.500'
        }
      }
    }
  }
};

// Typography and global styles
const fonts = {
  heading: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
  body: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'
};

const styles = {
  global: {
    body: {
      bg: 'gray.50',
      color: 'gray.800'
    }
  }
};
