import React, {Component} from "react";
import logoImg from "../img/home_logo.png"
import { Card, Logo, Form, Input, Button } from './AuthFormStyles';

export default class Home extends Component{


    render(){
        return(
            <div>
            <h3> Welcome to the Home page</h3>

            <Logo src={logoImg} />
            </div>
        );

    }


}
