import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import DatetimeRangePicker from 'react-bootstrap-datetimerangepicker';
import 'bootstrap-daterangepicker/daterangepicker.css';
import { Button as BootstrapButton } from 'react-bootstrap';

import ControlHeader from '../ControlHeader';


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
  startDate: PropTypes.any,
  endDate: PropTypes.any,
  ranges: PropTypes.any,
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
  startDate: moment().subtract(6, 'days'),
  endDate: moment(),
  ranges: {
    今天: [moment(), moment()],
    昨天: [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
    最近7天: [moment().subtract(6, 'days'), moment()],
    最近30天: [moment().subtract(29, 'days'), moment()],
    本月: [moment().startOf('month'), moment().endOf('month')],
    上月: [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
  },
};

export default class DatetimeRangePickerControl extends React.PureComponent {
  constructor(props) {
    super(props);
    this.handleEvent = this.handleEvent.bind(this);
    this.state = {
      ranges: this.getRanges(props),
      startDate: props.startDate,
      endDate: props.endDate,
    };
  }

  onChange(value) {
    this.props.onChange(value);
  }
  getRanges(props) {
    if (props.ranges) {
      return props.ranges;
    }
    return [];
  }
  getLabel() {
    const start = this.state.startDate.format('YYYY年MM月DD日');
    const end = this.state.endDate.format('YYYY年MM月DD日');
    let label = start + ' - ' + end;
    if (start === end) {
      label = start;
    }
    return label;
  }
  handleEvent(event, picker) {
    this.setState({
      startDate: picker.startDate,
      endDate: picker.endDate,
    });
    const label = this.getLabel();
    this.onChange(label);
  }
  render() {
    const label = this.getLabel();

    const locale = {
      format: 'YYYY-MM-DD',
      separator: ' - ',
      applyLabel: '确定',
      cancelLabel: '取消',
      weekLabel: 'W',
      customRangeLabel: '自定义',
      daysOfWeek: ['一', '二', '三', '四', '五', '六', '日'],
      monthNames: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'],
      firstDay: '一',
    };
    const buttonStyle = { width: '100%' };
    return (
      <div>
        {this.props.showHeader &&
          <ControlHeader {...this.props} />
        }
        {
          <DatetimeRangePicker
            startDate={this.state.startDate}
            endDate={this.state.endDate}
            ranges={this.state.ranges}
            onEvent={this.handleEvent}
            locale={locale}
          >
            <BootstrapButton className="selected-date-range-btn" style={buttonStyle}>
              <div className="pull-left">
                <i className="fa fa-calendar" />
                &nbsp;
                <span>
                  {label}
                </span>
              </div>
              <div className="pull-right">
                <i className="fa fa-angle-down" />
              </div>
            </BootstrapButton>
          </DatetimeRangePicker>
    }
      </div>
    );
  }
}

DatetimeRangePickerControl.propTypes = propTypes;
DatetimeRangePickerControl.defaultProps = defaultProps;
