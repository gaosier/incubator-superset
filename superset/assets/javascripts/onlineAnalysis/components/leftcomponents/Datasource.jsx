import React from 'react';
import {Table} from 'reactable';
import {
    Row, Col, Collapse, Label, FormControl, Modal,
    OverlayTrigger, Tooltip, Well,
} from 'react-bootstrap';
import {connect} from "react-redux";
import {
    get_all_datasource,
    get_datasource_columns,
    modify_datasource,
    get_all_filter_column
} from "../../actions/leftmenu";
import ColumnOption from '../../../components/ColumnOption';
import MetricOption from '../../../components/MetricOption';


class Datasource extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            showModal: false,
            filter: '',
            loading: true,
            showDatasource: false,
            first_load_column: true
        };
        this.toggleShowDatasource = this.toggleShowDatasource.bind(this);
        // this.onChange = this.onChange.bind(this);
        this.onEnterModal = this.onEnterModal.bind(this);
        this.toggleModal = this.toggleModal.bind(this);
        this.changeSearch = this.changeSearch.bind(this);
        this.setSearchRef = this.setSearchRef.bind(this);
        this.selectDatasource = this.selectDatasource.bind(this);
    }

    toggleModal() {
        this.setState({showModal: !this.state.showModal});
    }

    onEnterModal() {
        if (this.searchRef) {
            this.searchRef.focus();
        }
        this.props.get_all_datasource();
        this.setState({
            loading: false,
        });
    }

    setSearchRef(searchRef) {
        this.searchRef = searchRef;

    }

    changeSearch(event) {
        this.setState({filter: event.target.value});
    }

    selectDatasource(datasourceId, name) {
        this.setState({showModal: false});
        this.props.modify_datasource(datasourceId, name);
        this.props.get_all_filter_column(datasourceId);
        this.props.get_datasource_columns(datasourceId);
    }

    renderModal() {
        return (
            <Modal
                show={this.state.showModal}
                onHide={this.toggleModal}
                onEnter={this.onEnterModal}
                onExit={this.setSearchRef}
                bsSize="lg"
            >
                <Modal.Header closeButton>
                    <Modal.Title>选择一个数据源</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <div>
                        <FormControl
                            id="formControlsText"
                            inputRef={(ref) => {
                                this.setSearchRef(ref);
                            }}
                            type="text"
                            bsSize="sm"
                            value={this.state.filter}
                            placeholder={'Search / Filter'}
                            onChange={this.changeSearch}
                        />
                    </div>
                    {
                        <Table
                            columns={['name']}
                            className="table table-condensed"
                            data={this.props.leftmenu.slice.all_datasource.map(res => ({
                                name: (<a
                                    href="#"
                                    onClick={this.selectDatasource.bind(this, res.id, res.name)}
                                    className="datasource-link"
                                >{res.name}
                                </a>),
                                rawName: res.name
                            }))}
                            itemsPerPage={20}
                            filterable={['rawName']}
                            filterBy={this.state.filter}
                            hideFilterInput
                        />
                    }
                </Modal.Body>
            </Modal>);
    }

    toggleShowDatasource() {
        if (this.state.first_load_column) {
            this.props.get_datasource_columns(this.props.leftmenu.datasource_id);
        }
        ;

        this.setState({showDatasource: !this.state.showDatasource, first_load_column: false});
    }

    renderDatasource() {
        var b = 0;
        var c = 0;
        const datasource = this.props.leftmenu.slice.all_datasource_columns.columns.map(res => ({
            column_name: res[0] + "(" + res[1] + ")"
        }));
        const data = this.props.leftmenu.slice.all_datasource_columns.metrics.map(res => ({
            metric_name: res[0] + "(" + res[1] + ")"
        }));
        return (
            <div className="m-t-10">
                <Well className="m-t-0">
                    <div className="m-b-10">
                        <Label>
                            <i className="fa fa-database"/> mysql
                        </Label>
                        海量mysql数据库
                    </div>
                    <Row className="datasource-container">
                        <Col md={6}>
                            <strong>Columns</strong>
                            {datasource.map(col => (
                                <div key={b++}><ColumnOption column={col}/></div>
                            ))}
                        </Col>
                        <Col md={6}>
                            <strong>Metrics</strong>
                            {data.map(m => (
                                <div key={c++}><MetricOption metric={m} showFormula={false}/></div>
                            ))}
                        </Col>
                    </Row>
                </Well>
            </div>);
    }

    render() {
        return (
            <div>
                <OverlayTrigger
                    placement="right"
                    overlay={
                        <Tooltip id={'error-tooltip'}>点击选择其他的数据源</Tooltip>
                    }
                >
                    <Label onClick={this.toggleModal} style={{cursor: 'pointer'}} className="m-r-5">
                        {this.props.leftmenu.datasource_name}
                    </Label>
                </OverlayTrigger>
                <OverlayTrigger
                    placement="right"
                    overlay={
                        <Tooltip id={'toggle-datasource-tooltip'}>
                            点击显示数据源所有列
                        </Tooltip>
                    }
                >
                    <a href="#">
                        <i
                            className={`fa fa-${this.state.showDatasource ? 'minus' : 'plus'}-square m-r-5`}
                            onClick={this.toggleShowDatasource}
                        />
                    </a>
                </OverlayTrigger>
                <Collapse in={this.state.showDatasource}>
                    {this.renderDatasource()}
                </Collapse>
                {this.renderModal()}
            </div>);
    }
}

const mapStateToProps = (state) => {
    return {
        leftmenu: state.leftmenu,
    }
};
export default connect(mapStateToProps, {
    get_all_datasource,
    get_datasource_columns,
    modify_datasource,
    get_all_filter_column
})(Datasource);