import { extendTheme } from "@oxygen-ui/react";
import { Theme as OxygenTheme } from "@oxygen-ui/react/models";

const GuardioTheme: OxygenTheme = extendTheme({
  colorSchemes: {
    light: {
      palette: {
        primary: {
          main: "rgb(80, 166, 216)",
        },
        secondary: {
          main: "#f9ae2c",
        },
        background: {
          default: "#ffffff",
          paper: "#f8f9fa",
        },
        gradients: {
          primary: {
            stop1: "#rgb(80, 166, 216)",
            stop2: "#rgb(80, 166, 216)",
          },
        },
      },
    },
    dark: {
      palette: {
        primary: {
          main: "rgb(60, 146, 196)",
        },
        secondary: {
          main: "#e99e1c",
        },
        background: {
          default: "#121212",
          paper: "#1e1e1e",
        },
      },
    },
  },
  typography: {
    fontFamily: '"Roboto", sans-serif',
    h1: {
      fontFamily: '"Quicksand", sans-serif',
      fontWeight: 400,
    },
    h2: {
      fontFamily: '"Quicksand", sans-serif',
      fontWeight: 400,
    },
    h3: {
      fontFamily: '"Quicksand", sans-serif',
      fontWeight: 400,
    },
    h4: {
      fontFamily: '"Quicksand", sans-serif',
      fontWeight: 400,
    },
    h5: {
      fontFamily: '"Quicksand", sans-serif',
      fontWeight: 400,
    },
    h6: {
      fontFamily: '"Quicksand", sans-serif',
      fontWeight: 400,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          borderBottom: "3px solid",
          borderColor: "secondary.main",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: "10px", // Increased border radius for more curved edges
          display: "flex",
          alignItems: "center",
          borderColor: "primary.main",
          color: "primary.main",
        },
      },
      variants: [
        {
          props: { variant: "contained", color: "primary" },
          style: {
            backgroundColor: "rgb(80, 166, 216)",
            color: "white",
          },
        },
      ],
    },
  },
  customComponents: {
    AppShell: {
      properties: {
        mainBorderTopLeftRadius: "24px",
        navBarTopPosition: "80px",
      },
    },
    Navbar: {
      properties: {
        "chip-background-color": "#a333c8",
        "chip-color": "var(--oxygen-palette-primary-contrastText)",
      },
    },
  },
});

export default GuardioTheme;
