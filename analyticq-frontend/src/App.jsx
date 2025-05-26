import React from "react";
import { AppRoutes } from "routes/AppRoutes";
import store from "redux/store";
import { Provider as ReduxProvider } from "react-redux";

function App() {
  return (
    <ReduxProvider store={store}>
      <AppRoutes />
    </ReduxProvider>
  );
}

App.displayName = "App";

export default App;
