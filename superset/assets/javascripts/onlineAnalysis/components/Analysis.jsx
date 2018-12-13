import React, { Component } from 'react';
import LeftMenu from './LeftMenu';
import RightInfo from './RightInfo';
import {connect} from "react-redux";

class Analysis extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (

      <div className="App">
        <div className="container-fluid">
          <div className="row">
            <div className="col-sm-4">
              <LeftMenu />
            </div>

            <div className="col-sm-8">
              <RightInfo />
            </div>
          </div>
        </div>
      </div>
    );
  }


}

const mapStateToProps = (state) => {
    return {
        leftmenu:state.leftmenu,
    }
};
export default connect(mapStateToProps)(Analysis);
