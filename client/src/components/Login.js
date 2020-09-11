import React, {Component} from "react";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import axios from 'axios';
import './Login.css'
import logoImg from "../img/logo.png"
import { Card, Logo, Form, Input, Button } from './AuthFormStyles';
import { Redirect } from 'react-router-dom'; 




export default class Login extends Component {

    state = {
        email: "",
        password: "",
        loggedIn:false
    }


    handleEmailChange = (event) => {
        this.setState({email: event.target.value});
    };

    handlePasswordChange = (event) => {
        this.setState({password: event.target.value});
    };


 handleSubmit = (event) => {
     event.preventDefault();

    const user = {
            email: this.state.email,
            password: this.state.password,
      };


      axios.post('authlogin',user).then(res => {
          //console.log(res);
          console.log(res.data);
         localStorage.setItem('token', res.data.auth_token)
          this.setState({
            loggedIn:true
          });
          this.props.setUser(res.data.user)
          //this.props.history.push('/main');
          //return <Redirect to='/main' />
        //if (!!localStorage.token){
          //this.props.history.push('/login');
        //}
      }, (error) => {
          console.log(error);
          //throw error;
      });


 }//end handlesubmit



clearLogin = () => {
    this.setState({
        email:"",
        password:""
    });
};


render(){
    if(this.state.loggedIn){
        return <Redirect to={'/main'} />;
    }

        return (
            <div> 
                <h3>
                   Please Login to use the platform 
                </h3>
               <Card >
            <Logo src={logoImg} />
               <form onSubmit={this.handleSubmit}>
                    <div className="form-group">
                        <input type="email" name="email" className="form-control" onChange={this.handleEmailChange} placeholder="Enter Email" required  />
                    </div>

                <div className="form-group">
                            <input type="password" name="password" className="form-control" onChange={this.handlePasswordChange} placeholder="Enter Password" required />
                    </div>

                    <button type="submit" className="form-control btn btn-primary">
                       Login 
                    </button>
                </form>
            </Card>
            </div>
        );
    }




}

