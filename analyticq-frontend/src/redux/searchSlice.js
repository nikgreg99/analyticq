import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { getContextByRepoNamePrefix } from "services/contextService"; // Modify this import based on your service

// Initial state for search
const initialState = {
  searchQuery: "",
  searchResults: [],
  loading: false,
  error: null,
};

/**
 * Redux async thunk action creator that searches repositories by name prefix
 * @param {string} query - The prefix string to search repositories by
 * @returns {Promise<Object>} Promise that resolves to the response containing matching repositories
 * @throws {Error} When the API request fails, the error is handled by rejectWithValue
 */
export const searchByRepoNamePrefix = createAsyncThunk(
  "search/searchByRepoNamePrefix",
  async (query, { rejectWithValue }) => {
    try {
      const response = await getContextByRepoNamePrefix(query); // Fetch contexts filtered by prefix
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  },
);

const searchSlice = createSlice({
  name: "search",
  initialState,
  reducers: {
    setSearchQuery(state, action) {
      state.searchQuery = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(searchByRepoNamePrefix.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchByRepoNamePrefix.fulfilled, (state, action) => {
        state.searchResults = action.payload;
        state.loading = false;
      })
      .addCase(searchByRepoNamePrefix.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { setSearchQuery } = searchSlice.actions;

export default searchSlice.reducer;
