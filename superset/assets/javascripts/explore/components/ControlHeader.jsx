import React from 'react';
import PropTypes from 'prop-types';
import { ControlLabel, OverlayTrigger, Tooltip } from 'react-bootstrap';
import InfoTooltipWithTrigger from '../../components/InfoTooltipWithTrigger';
import { t } from '../../locales';
import { Button } from 'react-bootstrap';

const propTypes = {
  label: PropTypes.string,
  description: PropTypes.string,
  validationErrors: PropTypes.array,
  renderTrigger: PropTypes.bool,
  rightNode: PropTypes.node,
  leftNode: PropTypes.node,
  onClick: PropTypes.func,
  hovered: PropTypes.bool,
  tooltipOnClick: PropTypes.func,
  warning: PropTypes.string,
  clickfunc: PropTypes.func,
  opts: PropTypes.array,
  store: PropTypes.store,
  sorttext: PropTypes.string,
  button: PropTypes.string,
};

const defaultProps = {
  validationErrors: [],
  renderTrigger: false,
  hovered: false,
};

export default class ControlHeader extends React.Component {
  renderOptionalIcons() {
    if (this.props.hovered) {
      return (
        <span>
          {this.props.description &&
            <span>
              <InfoTooltipWithTrigger
                label={t('description')}
                tooltip={this.props.description}
                placement="top"
                onClick={this.props.tooltipOnClick}
              />
              {' '}
            </span>
          }
          {this.props.renderTrigger &&
            <span>
              <InfoTooltipWithTrigger
                label={t('bolt')}
                tooltip={t('Changing this control takes effect instantly')}
                placement="top"
                icon="bolt"
              />
              {' '}
            </span>
          }
        </span>);
    }
    return null;
  }
  render() {
    if (!this.props.label) {
      return null;
    }
    const labelClass = (this.props.validationErrors.length > 0) ? 'text-danger' : '';
    const opts=this.props.opts;
    const clickFunc=this.props.clickfunc;
    const buttStyle={
        padding:1
    };
    const store=this.props.store;
    class SortButton extends React.Component {
        constructor(props) {
          super(props);
          this.state = { text: props.text};
        }
        sortClick() {
            if(this.state.text==='排序'){
                store.dispatch({
                      type: 'start_sort',
                  });
            }
            else{
                store.dispatch({
                      type: 'end_sort',
                  });
            }
        }
        render(){
                return(
            <div className="pull-left">
             <Button
                bsSize="small"
                onClick={this.sortClick.bind(this)}
                style={buttStyle}
              >
                {this.state.text}
              </Button>
            </div>)
            }
    }
    const sortOptions=this.props.can_sort?(
        <SortButton text={this.props.sorttext}/>
    ):(null);
    const selectAll=this.props.button ?(
        <div className="pull-left">
         <Button
            bsSize="small"
            onClick={clickFunc.bind(this,opts)}
            style={buttStyle}
          >
            {t('Select all')}
          </Button>
        </div>
    ):(null);
    return (
      <div
        className="ControlHeader"
      >
        <div className="pull-left">
          <ControlLabel>
            {this.props.leftNode &&
              <span>{this.props.leftNode}</span>
            }
            <span
              onClick={this.props.onClick}
              className={labelClass}
              style={{ cursor: this.props.onClick ? 'pointer' : '' }}
            >
              {this.props.label}
            </span>
            {' '}
            {(this.props.warning) &&
              <span>
                <OverlayTrigger
                  placement="top"
                  overlay={
                    <Tooltip id={'error-tooltip'}>{this.props.warning}</Tooltip>
                  }
                >
                  <i className="fa fa-exclamation-circle text-danger" />
                </OverlayTrigger>
                {' '}
              </span>
            }
            {(this.props.validationErrors.length > 0) &&
              <span>
                <OverlayTrigger
                  placement="top"
                  overlay={
                    <Tooltip id={'error-tooltip'}>
                      {this.props.validationErrors.join(' ')}
                    </Tooltip>
                  }
                >
                  <i className="fa fa-exclamation-circle text-danger" />
                </OverlayTrigger>
                {' '}
              </span>
            }
            {this.renderOptionalIcons()}
          </ControlLabel>
          {selectAll}
          {sortOptions}
        </div>
        {this.props.rightNode &&
          <div className="pull-right">
            {this.props.rightNode}
          </div>
        }
        <div className="clearfix" />
      </div>
    );
  }
}

ControlHeader.propTypes = propTypes;
ControlHeader.defaultProps = defaultProps;
