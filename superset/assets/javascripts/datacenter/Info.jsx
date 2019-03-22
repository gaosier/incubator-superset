import React, {Component} from 'react';
import {OverlayTrigger, Tooltip,  FormControl, Modal} from 'react-bootstrap';
import { Button } from 'antd';
import { Table } from 'reactable';


export default class Info extends Component {
    constructor(props) {
        super(props);
        this.state = {
            showModal: false,
            filter: '',
            all_data: [],
            first_load:true,
            loading: true
        };
        this.renderTable = this.renderTable.bind(this);
        this.changeSearch = this.changeSearch.bind(this);
        this.onEnterModal = this.onEnterModal.bind(this);
        this.toggleModal = this.toggleModal.bind(this);
        this.setSearchRef = this.setSearchRef.bind(this);

    }

    getAllData() {
        let ajaxTimeOut = $.ajax({
            url: "/tablegroupview/search/table/",
            type: "GET",
            dataType: "json",
            timeout: 2000,
            success: function (data) {
                const datasources = data.map(ds => ({
                    name: ds[0],
                    表名: ds[1],
                    一级菜单: ds[2],
                    二级菜单: ds[3],
                  }))
                this.setState({ 
                    first_load:false,
                    datasources
                 });  
            }.bind(this),
            error: function (xhr, status, err) {
            },
        });
    }

    setSearchRef(searchRef){
        this.searchRef = searchRef;
    }

    toggleModal() {
            this.setState({showModal: !this.state.showModal})
    }

    onEnterModal(){
        if (this.searchRef) {
            this.searchRef.focus();
        }
        if(!this.state.datasources)
        {
            this.getAllData();
        }
        this.setState({
            loading: false,
        });
    }

    changeSearch(event) {
        this.setState({filter: event.target.value});
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
                    <Modal.Title>查看表分类</Modal.Title>
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
                            placeholder={'搜索 / 过滤'}
                            onChange={this.changeSearch}
                        />
                    </div>
                    {this.state.loading &&
                        <img
                        className="loading"
                        alt="Loading..."
                        src="/static/assets/images/loading.gif"
                        />
                    }
                    {this.state.datasources &&
                        <Table
                            columns={['表名','一级菜单','二级菜单']}
                            className="table table-condensed"
                            data = {this.state.datasources}
                            itemsPerPage={20}
                            filterable={['表名']}
                            filterBy={this.state.filter}
                            hideFilterInput
                        />
                    }
                </Modal.Body>
            </Modal>);
    }

    renderTable() {
        // 定义tooltip(鼠标移动至按钮出现提示语)
        const tooltip = (
            <Tooltip id="tooltip">
                显示记录.
            </Tooltip>
        );
        const tooltip_1 = (
            <Tooltip id="tooltip">
                编辑记录.
            </Tooltip>
        );
        const tooltip_2 = (
            <Tooltip id="tooltip">
                删除记录.
            </Tooltip>
        );
        if (this.props.infos.length == 0) {
            return (
                <div>
                    <b>没有找到任何记录</b>
                </div>
            )
        } else {
            return (
                <div>
                    <div className="table-responsive">
                        <table className="table table-hover">
                            <thead>
                            <tr>
                                <th className="action_checkboxes">
                                </th>
                                <th className="col-md-1 col-lg-1 col-sm-1"></th>
                                <th>表</th>
                                <th>数据库</th>
                                <th>修改人</th>
                                <th>
                                    {/*<a*/}
                                    {/*href="#"*/}
                                    {/*data-original-title="" title="">修改时间*/}
                                    {/*<i className="fa fa-arrows-v pull-right"></i></a>*/}
                                    修改时间
                                </th>
                            </tr>
                            </thead>
                            <tbody>
                            {
                                this.props.infos.map((info) => (
                                        <tr className key={info.id}>
                                            <td>
                                            </td>
                                            <td>
                                                <center>

                                                    <div className="btn-group btn-group-xs" style={{display: "flex"}}>
                                                        <OverlayTrigger placement="bottom" overlay={tooltip}>
                                                            <a href={"/mytablemodelview/show/" + info.id + "?_flt_0_group=1"}
                                                               className="btn btn-sm btn-default">
                                                                <i className="fa fa-search"></i></a>
                                                        </OverlayTrigger>
                                                        <OverlayTrigger placement="bottom" overlay={tooltip_1}>
                                                            <a href={"/mytablemodelview/edit/" + info.id + "?_flt_0_group=1"}
                                                               className="btn btn-sm btn-default">
                                                                <i className="fa fa-edit"></i></a>
                                                        </OverlayTrigger>
                                                    </div>
                                                </center>
                                            </td>
                                            <td dangerouslySetInnerHTML={{__html: info.name}}/>
                                            <td dangerouslySetInnerHTML={{__html: info.database}}/>
                                            <td dangerouslySetInnerHTML={{__html: info.changed_by}}/>
                                            <td dangerouslySetInnerHTML={{__html: info.modified}}/>
                                        </tr>
                                    )
                                )
                            }
                            </tbody>
                        </table>
                    </div>
                    <div className="form-actions-container">
                        <div className="btn-group">
                        </div>
                    </div>
                    <div className="pagination-container pull-right">
                        <strong>记录数:</strong> {this.props.infos.length}
                    </div>
                </div>
            )
        }
    }

    render() {
        return (
            <div className="col-lg-10 col-md-10 container">
                <div className="panel panel-primary">
                    <div className="panel-heading">
                        <Button type="primary" icon="search" id="filter" onClick={this.toggleModal} ghost>搜索</Button>
                        <h4 className="panel-title">{this.props.title}</h4>
                    </div>
                    { this.renderTable() }                
                </div>
                {this.renderModal()}
            </div>
        )
    }
}
