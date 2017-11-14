import React from 'react';
import PropTypes from 'prop-types';
import Select, { Creatable } from 'react-select';
import ControlHeader from '../ControlHeader';
import { t } from '../../../locales';

const propTypes = {
  choices: PropTypes.array,
  clearable: PropTypes.bool,
  description: PropTypes.string,
  freeForm: PropTypes.bool,
  isLoading: PropTypes.bool,
  label: PropTypes.string,
  multi: PropTypes.bool,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number, PropTypes.array]),
  showHeader: PropTypes.bool,
  optionRenderer: PropTypes.func,
  valueRenderer: PropTypes.func,
  valueKey: PropTypes.string,
  options: PropTypes.array,
  options_bak: PropTypes.array,
  clearAllText: PropTypes.string,
  clearValueText: PropTypes.string,
};

const defaultProps = {
  choices: [],
  clearable: true,
  description: null,
  freeForm: false,
  isLoading: false,
  label: null,
  multi: false,
  onChange: () => {},
  showHeader: true,
  optionRenderer: opt => opt.label,
  valueRenderer: opt => opt.label,
  valueKey: 'value',
  clearAllText: '清空',
  clearValueText: '清空',
};

// Handle `onPaste` so that users may paste in
// options as comma-delimited, slightly modified from
// https://github.com/JedWatson/react-select/issues/1672
function pasteSelect(props) {
  let pasteInput;
  return (
    <Select
      {...props}
      ref={(ref) => {
        // Creatable requires a reference to its Select child
        if (props.ref) {
          props.ref(ref);
        }
        pasteInput = ref;
      }}
      inputProps={{
        onPaste: (evt) => {
          if (!props.multi) {
            return;
          }
          evt.preventDefault();
          // pull text from the clipboard and split by comma
          const clipboard = evt.clipboardData.getData('Text');
          if (!clipboard) {
            return;
          }
          const values = clipboard.split(/[,]+/).map(v => v.trim());
          const options = values
            .filter(value =>
              // Creatable validates options
              props.isValidNewOption ? props.isValidNewOption({ label: value }) : !!value,
            )
            .map(value => ({
              [props.labelKey]: value,
              [props.valueKey]: value,
            }));
          if (options.length) {
            pasteInput.selectValue(options);
          }
        },
      }}
    />
  );
}
pasteSelect.propTypes = {
  multi: PropTypes.bool,
  ref: PropTypes.func,
};

export default class SelectControl extends React.PureComponent {
  constructor(props) {
    super(props);
    let options = this.getOptions(props);
    this.state = { options: options, options_bak: options};
    this.onChange = this.onChange.bind(this);
  }
  componentWillReceiveProps(nextProps) {
    if (nextProps.choices !== this.props.choices ||
        nextProps.options !== this.props.options) {
      const options = this.getOptions(nextProps);
      this.setState({ options });
    }
  }
  componentDidMount(){
    if(this.props.name == 'order_by_metric'){
        let optsMap={};
        this.props.choices.map((c) => {
            optsMap[JSON.parse(c[0])[0]]=c[2]
        });
        this.props.store.subscribe(() => {
            let state = this.props.store.getState();
            let data = state.data;
            if(state.type == 'order_by_metric'){
                let oldoptions = this.state.options.filter(function (option) {
                            let value1 = JSON.parse(option.value)[0];
                            if(optsMap[value1]!=state.name){
                                return true
                            }
                            return false
                });
                let options = this.state.options_bak.filter(function(option){
                            let value2 = JSON.parse(option.value)[0];
                            if(data.indexOf(value2)!=-1){
                                return true;
                            }
                            return false;
                        });
                this.setState({
                    data: data,
                    options: options.concat(oldoptions),
                    options_bak: this.state.options_bak
                });
            }
            }
         );
    }
    else if(this.props.name == 'groupby'||this.props.name=='metrics'){
        setTimeout(() => {
            this.props.store.dispatch({
                type: 'order_by_metric',
                name:this.props.name,
                data: this.props.value
            })
        }, 200);
    }
    else if(this.props.name=='granularity_sqla'){
        setTimeout(() => {
            this.props.store.dispatch({
                type: 'hidden_calendar',
                name:this.props.name,
                data: this.props.value
            })
        }, 200);}
  }
  onChange(opt) {
    let optionValue = opt ? opt[this.props.valueKey] : null;
    // if multi, return options values as an array
    if (this.props.multi) {
      optionValue = opt ? opt.map(o => o[this.props.valueKey]) : null;
    }
    if(this.props.name == 'groupby'||this.props.name=='metrics'){
        this.props.store.dispatch({
            type: 'order_by_metric',
            name:this.props.name,
            data: optionValue
        });
    }
    if(this.props.name=='granularity_sqla'){
        this.props.store.dispatch({
            type: 'hidden_calendar',
            name:this.props.name,
            data: optionValue
        });
    }
    this.props.onChange(optionValue);
  }
  getOptions(props) {
    if (props.options) {
      return props.options;
    }
    // Accepts different formats of input
    const options = props.choices.map((c) => {
      let option;
      if (Array.isArray(c)) {
        const label = c.length > 1 ? c[1] : c[0];
        option = {
          value: c[0],
          label,
        };
      } else if (Object.is(c)) {
        option = c;
      } else {
        option = {
          value: c,
          label: c,
        };
      }
      return option;
    });
    if (props.freeForm) {
      // For FreeFormSelect, insert value into options if not exist
      const values = options.map(c => c.value);
      if (props.value) {
        let valuesToAdd = props.value;
        if (!Array.isArray(valuesToAdd)) {
          valuesToAdd = [valuesToAdd];
        }
        valuesToAdd.forEach((v) => {
          if (values.indexOf(v) < 0) {
            options.push({ value: v, label: v });
          }
        });
      }
    }
    return options;
  }
  render() {
    //  Tab, comma or Enter will trigger a new option created for FreeFormSelect
    const selectProps = {
      multi: this.props.multi,
      name: `select-${this.props.name}`,
      placeholder: t('Select %s', this.state.options.length),
      options: this.state.options,
      value: this.props.value,
      labelKey: this.props.labelKey||'label',
      valueKey: this.props.valueKey,
      autosize: false,
      clearable: this.props.clearable,
      isLoading: this.props.isLoading,
      onChange: this.onChange,
      optionRenderer: this.props.optionRenderer,
      valueRenderer: this.props.valueRenderer,
      clearAllText: this.props.clearAllText,
      clearValueText: this.props.clearValueText,
    };
    //  Tab, comma or Enter will trigger a new option created for FreeFormSelect
    const selectWrap = this.props.freeForm ? (
      <Creatable {...selectProps}>
        {pasteSelect}
      </Creatable>
    ) : (
      pasteSelect(selectProps)
    );
    return (
      <div>
        {this.props.showHeader &&
          <ControlHeader {...this.props} opts={this.state.options} clickfunc={this.onChange}/>
        }
        {selectWrap}
      </div>
    );
  }
}

SelectControl.propTypes = propTypes;
SelectControl.defaultProps = defaultProps;
