import React from 'react';
import PropTypes from 'prop-types';
import {CompactPicker} from 'react-color';
import {Button} from 'react-bootstrap';
import SelectControl from './SelectControl';

const FONT_OPTIONS = [
    'normal',
    'bold',
];
const propTypes = {
    name: PropTypes.string.isRequired,
    value: PropTypes.array,
    label: PropTypes.string,
    description: PropTypes.string,
    onChange: PropTypes.func,
};
const defaultProps = {
    value: [{}],
    onChange: () => {
    },
};
export default class RowControl extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            value: props.value,
        };
    }

    onSelectChange(value) {
        this.setState(value);
    }

    onValueChange(type, index, newValue) {
        const value = this.state.value[index]; // 待查看 之前为props
        if (!(type in value)) {
            value[type] = null;
        }
        value[type] = newValue;
        const now_value = this.state.value;
        now_value[index] = value;
        this.setState({
            value:now_value
        });
        this.props.onChange(now_value);
    }

    onCancel(colorChoice,index) {
        const value = this.state.value[index]; // 待查看 之前为props
        if (!(colorChoice in value)) {
            value[colorChoice] = {};
        }
        value[colorChoice] = {};
        const now_value = this.state.value;
        now_value[index] = value;
        this.setState({
            value:now_value
        });
        this.props.onChange(now_value);
    }

    render_color() {
        return this.state.value.map((dum, index) => {
            const value = dum === null ? {} : dum;
            const basements = (
                'basements' in value
            ) ? value.basements : null;
            const coloringOption = (
                'coloringOption' in value
            ) ? value.coloringOption : {};
            const fontOption = (
                'fontOption' in value
            ) ? value.fontOption : null;
            return(
                <div key={index}>
                    <table className="table table-bordered" style={{fontSize: '12px'}}>
                    <tbody>
                    <tr>
                        <td><span>行内容</span></td>
                        <td>
                            <SelectControl
                                multi
                                freeForm
                                name="contains-value"
                                clearable
                                onChange={this.onValueChange.bind(this, 'basements',index)}
                                value={basements}
                            />
                        </td>
                    </tr>
                    <tr>
                        <td><span>着色选项</span></td>
                        <td>
                            <CompactPicker
                                color={coloringOption}
                                onChangeComplete={this.onValueChange.bind(this, 'coloringOption',index)}
                            />
                            <Button
                                id="cancel-row-color-button"
                                style={{marginLeft: '15px'}}
                                bsSize="xs"
                                onClick={this.onCancel.bind(this, 'coloringOption',index)}
                            >
                                <i className="fa fa-close"/> 重置颜色
                            </Button>
                        </td>
                    </tr>
                    <tr>
                        <td><span>字体选项</span></td>
                        <td>
                            <SelectControl
                                name={'___fontOption'}
                                default={FONT_OPTIONS[0]}
                                choices={FONT_OPTIONS}
                                clearable
                                onChange={this.onValueChange.bind(this, 'fontOption',index)}
                                value={fontOption}
                            />
                        </td>
                    </tr>
                    </tbody>
                </table>
                </div>
            )
        })
    }

    incr_cmp(){
        const new_value = this.state.value.concat({});
        this.setState({
            value:new_value
        })
    }

    render() {
        return (
            <div>
                { this.render_color() }
                <Button onClick={this.incr_cmp.bind(this)}><i className="fa fa-plus"></i>增加过滤条件</Button>
            </div>
        );
    }
}
RowControl.propTypes = propTypes;
RowControl.defaultProps = defaultProps;