import React, {Component} from "react";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import { Card, Logo, Form, Input, Button } from './AuthFormStyles';
import axios from 'axios';

export default class Register extends Component {


    state = {
        firstname: "",
        lastname: "",
        email: "",
        password: "",
        confirm: "",
        errors: {}
    }

    handleFnameChange = (event) => {
        this.setState({firstname: event.target.value});
    };

    handleLnameChange = (event) => {
        this.setState({lastname: event.target.value});
    };

    handleEmailChange = (event) => {
        this.setState({email: event.target.value});
    };

    handlePasswordChange = (event) => {
        this.setState({password: event.target.value});
    };

    handleConfirmChange = (event) => {
        this.setState({confirm: event.target.value});
    };


  handleSubmit = event => {
      event.preventDefault();

      
      const user = {
            firstname: this.state.firstname,
            lastname: this.state.lastname,
            email: this.state.email,
            password: this.state.password,
            confirm: this.state.confirm
      };

      
      if(this.validate()){
      axios.post('http://localhost:5000/register',user).then(res => {
          console.log(res);
          console.log(res.data);
          this.props.history.push('/login');
      }, (error) => {
          console.log(error);
      });
     }
  };


    validate(){

        let confirm = this.state.confirm;
        let errors = {};
        let isValid = true;

    if (this.state.password != this.state.confirm){
        isValid = false;
        errors["confirm_password"] = "Passwords don't match";
      }

        this.setState({
            errors:errors
        });

        return isValid;
    }


    render(){
        return (
            <div> 
                <h3>
                   Please Register to use the platform 
                </h3>
            <Card>
               <form onSubmit={this.handleSubmit}>
                    <div className="form-group">
                        <input type="text" name="firstname" className="form-control" onChange={this.handleFnameChange} placeholder="Enter Firstname" required/>
                    </div>

                    <div className="form-group">
                        <input type="text" name="lastname" className="form-control" onChange={this.handleLnameChange} placeholder="Enter Lastname" required />
                    </div>

                    <div className="form-group">
                        <input type="email" name="email" className="form-control" onChange={this.handleEmailChange} placeholder="Enter Email" required  />
                    </div>

                <div className="form-group">
                        <input type="password" name="password" className="form-control" onChange={this.handlePasswordChange} placeholder="Enter Password" required />
                    </div>

                <div className="form-group">
                        <input type="password" name="confirm" className="form-control" onChange={this.handleConfirmChange} placeholder="Confirm Password" required />
                    </div>
    <div className="text-danger">{this.state.errors.confirm_password}</div>

                    <button type="submit" className="form-control btn btn-primary">
                       Register 
                    </button>
                </form>
            </Card>
            </div>
        );
    }



}
