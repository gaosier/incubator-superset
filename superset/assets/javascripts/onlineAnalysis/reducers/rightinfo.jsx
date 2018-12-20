import {LOG} from '../constants/leftmenu'

const rightinfo = (state = {}, action = {}) => {
    switch (action.type) {
        case LOG:
            const name = action.name;
            return Object.assign({}, state, {name: action.res.data});
        default:
            return state;
    }
}

export default rightinfo;