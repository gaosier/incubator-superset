import React from 'react';
import PropTypes from 'prop-types';
import VirtualizedSelect from 'react-virtualized-select';
import Select, { Creatable } from 'react-select';
import ControlHeader from '../ControlHeader';
import { t } from '../../../locales';
import VirtualizedRendererWrap from '../../../components/VirtualizedRendererWrap';
import OnPasteSelect from '../../../components/OnPasteSelect';
import SortableComponent from '../../../../javascripts/explore/components/controls/ReactSortableHoc';
import {createStore} from 'redux'

const propTypes = {
  choices: PropTypes.array,
  clearable: PropTypes.bool,
  description: PropTypes.string,
  disabled: PropTypes.bool,
  freeForm: PropTypes.bool,
  isLoading: PropTypes.bool,
  label: PropTypes.string,
  multi: PropTypes.bool,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func,
  onFocus: PropTypes.func,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number, PropTypes.array]),
  showHeader: PropTypes.bool,
  optionRenderer: PropTypes.func,
  valueRenderer: PropTypes.func,
  valueKey: PropTypes.string,
  options: PropTypes.array,
  placeholder: PropTypes.string,
  noResultsText: PropTypes.string,
  refFunc: PropTypes.func,
  filterOption: PropTypes.func,
};

const defaultProps = {
  choices: [],
  clearable: true,
  description: null,
  disabled: false,
  freeForm: false,
  isLoading: false,
  label: null,
  multi: false,
  onChange: () => {},
  onFocus: () => {},
  showHeader: true,
  optionRenderer: opt => opt.label,
  valueRenderer: opt => opt.label,
  valueKey: 'value',
  clearAllText: '清空',
  clearValueText: '清空',
  noResultsText: t('No results found'),
};

export default class SelectControl extends React.PureComponent {
  constructor(props) {
    super(props);
    this.state = { options: this.getOptions(props),sorttext:"排序" };
    this.onChange = this.onChange.bind(this);
    function reducer(state = {}, action) {
      return action;
    }
    this.store = createStore(reducer);
  }
  componentWillReceiveProps(nextProps) {
    if (nextProps.choices !== this.props.choices ||
        nextProps.options !== this.props.options) {
      const options = this.getOptions(nextProps);
      this.setState({ options });
    }
  }
  componentDidMount(){
    this.store.subscribe(() => {
      let state = this.store.getState();
      if(state.type==="show_vals"){
          this.setState({
                display:"block",
                sorttext:'排序',
                    });
          this.onChange(state.data_list)
      }
      else if (state.type==="start_sort"){
          this.setState({
              display:'none',
              sorttext:'完成'
          });
          this.store.dispatch({
              type:"show_sort",
              data_list:this.props.value
          });
      }
  });
  }
  onChange(opt){
    let optionValue = opt ? opt[this.props.valueKey] : null;
    // if multi, return options values as an array
    if (this.props.multi) {
      optionValue = opt ? opt.map(o => o[this.props.valueKey]) : null;
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
    const placeholder = this.props.placeholder || t('%s option(s)', this.state.options.length);
    const selectProps = {
      multi: this.props.multi,
      name: `select-${this.props.name}`,
      placeholder,
      options: this.state.options,
      value: this.props.value,
      labelKey: this.props.labelKey||'label',
      valueKey: this.props.valueKey,
      autosize: false,
      clearable: this.props.clearable,
      isLoading: this.props.isLoading,
      onChange: this.onChange,
      onFocus: this.props.onFocus,
      optionRenderer: VirtualizedRendererWrap(this.props.optionRenderer),
      valueRenderer: this.props.valueRenderer,
      clearAllText: this.props.clearAllText,
      clearValueText: this.props.clearValueText,
      noResultsText: this.props.noResultsText,
      selectComponent: this.props.freeForm ? Creatable : Select,
      disabled: this.props.disabled,
      refFunc: this.props.refFunc,
      filterOption: this.props.filterOption,
    };
    const sortComp=this.props.can_sort?(
          <SortableComponent items={this.props.value} opts={this.state.options} labelKey={this.props.labelKey||'label'} valueKey={this.props.valueKey} store={this.store}/>
      ):(null);
    return (
      <div>
        {this.props.showHeader &&
          <ControlHeader {...this.props} opts={this.state.options} clickfunc={this.onChange} store={this.store} sorttext={this.state.sorttext}/>
        }
        {sortComp}
        <div style={{display:this.state.display}}>
          <OnPasteSelect {...selectProps} selectWrap={VirtualizedSelect} />
        </div>
      </div>
    );
  }
}

SelectControl.propTypes = propTypes;
SelectControl.defaultProps = defaultProps;
