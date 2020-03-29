import dataJson from "../clusters/clusters_result.json";
const axios = require("axios");

const INITIAL_STATE = {
  load: true,
  data: [],
  success: false,
  date: null
};
export const dataReducer = (state = INITIAL_STATE, action) => {
  switch (action.type) {
    case "LOAD_DATA":
      return INITIAL_STATE;

    case "RECEIVE_DATA":
      return {
        load: false,
        data: action.payload,
        success: true,
        date: action.date
      };

    default:
      return state;
  }
};
