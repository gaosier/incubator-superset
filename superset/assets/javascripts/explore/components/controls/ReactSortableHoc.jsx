import React, {Component} from 'react';
import {render} from 'react-dom';
import {SortableContainer, SortableElement, arrayMove} from 'react-sortable-hoc';
import { nav } from 'react-bootstrap';
const SortableItem = SortableElement(({value}) =>
  <li role={"presentation"}>{value}</li>
);

const SortableList = SortableContainer(({items}) => {
  return (
    <nav>
      <ul className={"nav nav-pills nav-stacked"} style={{paddingLeft: 15}}>
        {items.map((value, index) => (
          <SortableItem key={`item-${index}`} index={index} value={value} />
        ))}
      </ul>
    </nav>
  );
});

export default class SortableComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = { items: props.items,display:'none'};
  }

  onSortEnd({oldIndex, newIndex}){
    this.setState({
      items: arrayMove(this.state.items, oldIndex, newIndex),
    });
  };
  componentDidMount(){
    this.props.store.subscribe(() => {
      let state = this.props.store.getState();
      const data_list=state.data_list;
      if(state.type==='show_sort'){
        let items=[];
        let value_list=[];
        let lable_list=[];
        this.props.opts.map(o=>{
          value_list.push(o[this.props.valueKey]);
          lable_list.push(o[this.props.labelKey]);
        });
        data_list.map(o=>{
          let index=value_list.indexOf(o);
          if(index>=0){
             items.push(lable_list[index])
          }
        });
        this.setState({
            display:'block',
            items:items
        })
      }
      else if (state.type==='end_sort'){
        this.setState({
            display:'none'
        });
        let opt=[] ;
        const opVal=this.state.items;
        opVal.map(o=>{
          this.props.opts.map(i=>{
            if(i[this.props.labelKey]===o){
              opt.push(i)
            }
          })
        });

        this.props.store.dispatch({
            type: 'show_vals',
            data_list:opt
        })
        }
    })
  }
  render() {
    // if(!this.state.items instanceof Array || this.state.items.length < 1){
    //   return null
    // }
    // else {
      return(
      <div style={{display:this.state.display}}>
        <SortableList items={this.state.items} onSortEnd={this.onSortEnd.bind(this)}/>
      </div>);
    // }

}}
