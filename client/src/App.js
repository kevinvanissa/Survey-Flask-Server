import React, {Component} from 'react';
import logo from './logo.svg';
import Register from './components/Register';
import Login from './components/Login';
import Home from './components/Home';
import Main from './components/Main';
import axios from 'axios';

import { 
	BrowserRouter as Router, 
	Route, 
	Link, 
	Switch 
} from 'react-router-dom'; 

import './App.css';

import { library } from "@fortawesome/fontawesome-svg-core";
import { faTrash, faPlus, faEdit } from "@fortawesome/free-solid-svg-icons";
library.add(faTrash, faEdit, faPlus);




export default  class  App extends Component {


    state={}
componentDidMount = () => {
        const config = {
            headers:{
            'x-access-token': localStorage.getItem('token')
            }
        };


        //axios.get('http://localhost:5000/user',config).then( res => {
        axios.get('user',config).then( res => {
            this.setState({
                user: this.setUser(res.data)
            });
            console.log(res);
        },

        err => {
            console.log(err);
        }
      )
    };



    setUser = user => {
        this.setState({
            user:user
        });
    };



  handleLogout = () => {
    localStorage.clear();
    this.setUser(null);

  }


  render(){

    let buttons;
if(this.state.user){
    buttons=(<span> 
            <li className="nav-item"> <Link  className="nav-link" to="/main">Main</Link> </li>
             <li className="nav-item">   <Link to="/" onClick={this.handleLogout}>Log out</Link> </li>
        </span>
            )

          }else{

    buttons=( <span>  
                <li className="nav-item"><Link className="nav-link" to="/">Home</Link> </li>
               <li className="nav-item"> <Link className="nav-link" to="/login">Login</Link> </li> 
               <li className="nav-item"> <Link className="nav-link" to="/register">Register</Link> </li>
            </span>
        
            )
          }


  return (
      <Router>
        <div className="App">

          <nav className="navbar navbar-expand-sm  navbar-dark bg-dark">
                <ul className="navbar-nav">
                {buttons}
               </ul>
            </nav>
            <Switch> 
              <Route exact path='/' component={Home}></Route> 
              <Route exact path='/register' component={Register}></Route> 
              <Route exact path='/login' component={ () => <Login setUser={this.setUser}   />  }></Route> 
              <Route exact path='/main' component={ () => <Main user={this.state.user} /> } /> 
            </Switch> 

        </div>
      </Router>
      );
  }
  } 

