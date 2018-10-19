import React, {Component} from 'react';
import {OverlayTrigger, Tooltip} from 'react-bootstrap';


export default class Info extends Component {
    constructor(props) {
        super();

    }

    render() {
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
        return (
            <div className="col-lg-10 col-md-10 container">
                <div className="panel panel-primary">
                    <div className="panel-heading">
                        <h4 className="panel-title">{this.props.title}</h4>
                    </div>
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
                                    <th><a
                                        href="#"
                                        data-original-title="" title="">Modified
                                        <i className="fa fa-arrows-v pull-right"></i></a></th>
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
                </div>
            </div>
        )
    }
}
