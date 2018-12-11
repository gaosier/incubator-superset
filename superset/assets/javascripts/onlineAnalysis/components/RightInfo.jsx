import React, { Component } from 'react'
import { Tabs, Tab } from 'react-bootstrap';


export default class RightInfo extends Component {
    render() {
        return (
            <div>
                <Tabs defaultActiveKey={1} id="uncontrolled-tab-example" >
                    <Tab eventKey={1} title={"日志展示"}>
                    </Tab>
                    <Tab eventKey={2} title={"图表展示"}>
                    </Tab>
                    <Tab eventKey={3} title={"业务方数据展示"}>
                    </Tab>
                </Tabs>
            </div>
        )
    }
}
