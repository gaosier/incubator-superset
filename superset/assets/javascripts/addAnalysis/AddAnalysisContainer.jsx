/**
 * Created by majing on 2018/11/23.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { Button, Panel, Grid, Row, Col } from 'react-bootstrap';
import Select from 'react-virtualized-select';

const propTypes = {
  datasources: PropTypes.arrayOf(PropTypes.shape({
    label: PropTypes.string.isRequired,
    value: PropTypes.string.isRequired,
  })).isRequired,
};

export default class AddSliceContainer extends React.PureComponent {
  constructor(props) {
    super(props);
    this.state = {
    };
  }

  exploreUrl() {
    const formData = encodeURIComponent(
      JSON.stringify({
        datasource: this.state.datasourceValue,
      }));
    return `/superset/explore/?form_data=${formData}`;
  }

  gotoSlice() {
    window.location.href = this.exploreUrl();
  }

  changeDatasource(e) {
    this.setState({
      datasourceValue: e.value,
      datasourceId: e.value.split('__')[0],
      datasourceType: e.value.split('__')[1],
    });
  }

  isBtnDisabled() {
    return !(this.state.datasourceId);
  }

  render() {
    return (
      <div className="container">
        <Panel header={<h3>创建分析模型</h3>}>
          <Grid>
            <Row>
              <Col xs={12} sm={6}>
                <div>
                  <p>选择数据源</p>
                  <Select
                    clearable={false}
                    name="select-datasource"
                    onChange={this.changeDatasource.bind(this)}
                    options={this.props.datasources}
                    placeholder={'选择数据源'}
                    value={this.state.datasourceValue}
                  />
                </div>
                <br />
                <br />
                <Button
                  bsStyle="primary"
                  disabled={this.isBtnDisabled()}
                  onClick={this.gotoSlice.bind(this)}
                >
                  创建分析模型
                </Button>
                <br /><br />
              </Col>
            </Row>
          </Grid>
        </Panel>
      </div>
    );
  }
}

AddSliceContainer.propTypes = propTypes;

