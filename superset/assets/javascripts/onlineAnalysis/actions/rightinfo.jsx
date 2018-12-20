// 根据模型id获取到img,log所有的

import axios from "axios/index";
import {LOG, PARAM, IMAGE} from "../constants/leftmenu";

export const get_log = (name, id) => {
    return dispatch => {
        axios.get('/online/log/' + name + '/?log_dir_id=' + id)
            .then(res => {
                dispatch(save_log(res.data))
            })
            .catch(error => {
            })
    }
};

export const save_log = (res) => {
    return {
        type: LOG,
        res
    }
};

export const get_parms = (name, id) => {
    return dispatch => {
        axios.get('/online/param/' + name + '/?log_dir_id=' + id)
            .then(res => {
                dispatch(save_param(res.data))
            })
            .catch(error => {
            })
    }
};

export const save_param = (res) => {
    return {
        type: PARAM,
        res
    }
};

export const get_image = (name, id) => {
    return dispatch => {
        axios.get('/online/image/' + name + '/?log_dir_id=' + id)
            .then(res => {
                dispatch(save_image(res.data))
            })
            .catch(error => {
            })
    }
};

export const save_image = (res) => {
    return {
        type: IMAGE,
        res
    }
};