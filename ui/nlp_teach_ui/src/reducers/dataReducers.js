const dataReducer = (
  state = {
    load: true,
    data: []
  },
  action
) => {
  switch (action.type) {
    case "LOAD_DATA":
      loadData(action.date);
      state.data = action.document;
      state.load = false;
      return state;

    default:
      return state;
  }
};

const loadData = date => {
  /*getDataFromServer(date).then((el)=>{

        return el;

    })
    */
};
