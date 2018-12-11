import React, {Component} from 'react';

class DatasourceMenu extends Component {

    render() {
        return (
            <Panel header="数据源/模型选择" key="1">
                <div>
                    <span>数据源</span>
                    <br/>
                    <div>
                        <Select defaultValue={'1'} showSearch style={{width: 200}}
                                searchPlaceholder="输入"
                        >
                            <Option value="jack">jack</Option>
                            <Option value="lucy">lucy</Option>
                            <Option value="disabled">disabled</Option>
                            <Option value="yiminghe">yiminghe</Option>
                        </Select>
                        <DatasourceControl name={this.props.leftmenu.datasource.name} value={'nihao'}
                                           datasource={this.props.leftmenu.datasource}/>
                    </div>
                </div>
                <div>
                    <span>模型名称</span>
                    <div>
                        <Select
                            defaultValue="lucy"
                            showSearch
                            style={{width: 200}}
                            searchPlaceholder="输入"
                            onFocus={this.show_all.bind(this)}
                        >
                            {this.render_options()}
                        </Select>
                    </div>
                </div>
                <div>
                    <span>版本名称</span>
                    <div>
                        <Select defaultValue="lucy" showSearch style={{width: 200}}
                                searchPlaceholder="输入"
                        >
                            <Option value="jack">jack</Option>
                            <Option value="lucy">lucy</Option>
                            <Option value="disabled">disabled</Option>
                            <Option value="yiminghe">yiminghe</Option>
                        </Select>
                    </div>
                </div>
            </Panel>
        );
    }
}

export default DatasourceMenu;
