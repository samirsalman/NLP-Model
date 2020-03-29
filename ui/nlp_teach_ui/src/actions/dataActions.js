const axios = require("axios");

export function getData(date) {
  return dispatch => {
    dispatch({ type: "LOAD_DATA" });
    if (date === null) {
      return dispatch({
        type: "RECEIVE_DATA",
        payload: [],
        load: false,
        date: date
      });
    } else {
      axios.get(`http://localhost:3000/lessons/${date}`).then(res =>
        res !== null && res.data !== []
          ? dispatch({
              type: "RECEIVE_DATA",
              payload: res.data,
              date: date,
              load: false
            })
          : dispatch({
              type: "RECEIVE_DATA",
              payload: [],
              date: date,
              load: false
            })
      );
    }
  };
}

export const success = data => {
  return {
    type: "SUCCESS",
    payload: data
  };
};
