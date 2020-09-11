import React, {Component} from "react";


export default class Main extends Component{

    render(){

        if(this.props.user){
            return(
                <h3> Hello {this.props.user.firstname} {this.props.user.lastname} </h3>
            );

        }

        return(
            <h3> Welcome to the main page</h3>
        );

    }


}
