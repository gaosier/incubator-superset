import { LOG } from '../constants/leftmenu'

const rightinfo = (state = {}, action = {}) => {
  switch(action.type) {
      case LOG:
          const name = action.name;
          console.log(1111,Object.assign({}, state, {log: action.res.data}));
          return Object.assign({}, state, {name: action.res.data});
    default: return state;
  }
}

export default rightinfo;