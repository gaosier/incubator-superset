import React from 'react';
import PropTypes from 'prop-types';
import { ControlLabel, OverlayTrigger, Tooltip } from 'react-bootstrap';
import InfoTooltipWithTrigger from '../../components/InfoTooltipWithTrigger';
import { Button } from 'react-bootstrap';
import { t } from '../../locales';

const propTypes = {
  label: PropTypes.string.isRequired,
  description: PropTypes.string,
  validationErrors: PropTypes.array,
  renderTrigger: PropTypes.bool,
  rightNode: PropTypes.node,
  leftNode: PropTypes.node,
  hovered: PropTypes.bool,
};

const defaultProps = {
  validationErrors: [],
  renderTrigger: false,
  hovered: false,
};

export default function ControlHeader({
    label, description, validationErrors, renderTrigger, leftNode, rightNode }) {
  const hasError = (validationErrors.length > 0);
  const opts=arguments[0].opts;
  const clickFunc=arguments[0].clickfunc;
  const buttStyle={
      padding:1
  };
  const store=arguments[0].store;
  const hovered=arguments[0].hovered;
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
  const sortOptions=arguments[0].can_sort?(
      <SortButton text={arguments[0].sorttext}/>
  ):(null);
  const selectAll=arguments[0].button ?(
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
  function renderOptionalIcons() {
    if (hovered) {
      return (
        <span>
          {description &&
            <span>
              {' '}
              <InfoTooltipWithTrigger
                label={label}
                tooltip={description}
              />
            </span>
          }
          {/*{renderTrigger &&*/}
            {/*<span>*/}
              {/*<InfoTooltipWithTrigger*/}
                {/*label={t('bolt')}*/}
                {/*tooltip={t('Changing this control takes effect instantly')}*/}
                {/*placement="top"*/}
                {/*icon="bolt"*/}
              {/*/>*/}
              {/*{' '}*/}
            {/*</span>*/}
          {/*}*/}
        </span>);
    }
    return null;
  }
  return (
    <div>
      <div className="pull-left">
        <ControlLabel>
          {hasError ?
            <strong className="text-danger">{label}</strong> :
            <span>{label}</span>
          }
          {' '}
          {(validationErrors.length > 0) &&
            <span>
              <OverlayTrigger
                placement="right"
                overlay={
                  <Tooltip id={'error-tooltip'}>
                    {validationErrors.join(' ')}
                  </Tooltip>
                }
              >
                <i className="fa fa-exclamation-circle text-danger" />
              </OverlayTrigger>
              {' '}
            </span>
          }
          {/*{description &&*/}
            {/*<span>*/}
              {/*<InfoTooltipWithTrigger label={label} tooltip={description} />*/}
              {/*{' '}*/}
            {/*</span>*/}
          {/*}*/}
          {renderTrigger &&
            <span>
              <OverlayTrigger
                placement="right"
                overlay={
                  <Tooltip id={'rendertrigger-tooltip'}>
                    Takes effect on chart immediatly
                  </Tooltip>
                }
              >
                <i className="fa fa-bolt text-muted" />
              </OverlayTrigger>
              {' '}
            </span>
          }
          {leftNode &&
            <span>{leftNode}{' '}</span>
          }
        </ControlLabel>
      </div>
      {selectAll}
      {sortOptions}
      <div className="pull-left">
      {renderOptionalIcons()}
      </div>
      {rightNode &&
        <div className="pull-right">
          {rightNode}
        </div>
      }
      <div className="clearfix" />
    </div>
  );
}

ControlHeader.propTypes = propTypes;
ControlHeader.defaultProps = defaultProps;
