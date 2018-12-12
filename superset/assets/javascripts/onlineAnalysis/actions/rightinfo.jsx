
// 根据模型id获取到img,log所有的

import axios from "axios/index";
import {LOG} from "../constants/leftmenu";

export const get_log= (name, id) =>{
    return dispatch => {
            axios.get('/online/log/'+name+'/?log_dir_id='+id)
                .then(res => {
                    console.log(res);
                    res.data = res.data.replace('\n', '\n');
                    dispatch(save_log(res.data,name))
                })
                .catch(error => {
                })
        }
};

export const save_log = (res,name) =>{
    return {
        type:LOG,
        res,
        name
    }
};
