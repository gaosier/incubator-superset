const rightinfo = (state = [], action = {}) => {
  switch(action.type) {
  	case "DATAINFO":
  		return action.info;
    default: return state;
  }
}

export default rightinfo;