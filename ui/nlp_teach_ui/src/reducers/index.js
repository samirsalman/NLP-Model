import { combineReducers } from "redux";
import { dataReducer } from "./dataReducers";

const allReducers = combineReducers({
  data: dataReducer
});

export default allReducers;
