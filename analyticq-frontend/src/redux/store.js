import { configureStore } from '@reduxjs/toolkit';
import searchReducer from './searchSlice';

/**
 * Redux store configuration.
 * @constant {Object} store
 * @description Creates a Redux store using configureStore from @reduxjs/toolkit.
 * Contains search reducer for managing search-related state.
 */
const store = configureStore({
  reducer: {
    search: searchReducer,
  },
});

export default store;
