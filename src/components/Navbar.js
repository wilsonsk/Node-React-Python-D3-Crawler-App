import React from 'react';

class Navbar extends React.Component {
    constructor(props) {
        super(props);
    }
    
    render() {
        return(
            <nav className="navbar navbar-inverse navbar-fixed-top">
              <div className="container">
                <div className="navbar-header">
                  <a className="navbar-brand" href="#">Andromeda Graphical Crawler</a>
                </div>
              </div>
            </nav>
        )
    }
}

export default Navbar;