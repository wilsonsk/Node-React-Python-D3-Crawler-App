import React from 'react';

class Footer extends React.Component {
    constructor(props) {
        super(props);
    }
    
    render() {
        return(
            <div className="container theme-showcase head" role="main">
              <div className="jumbotron">
                <p>Copyright 2017 - Team Andromeda (Maxwell Goldberg, Kevin Pardew, and Skyler Wilson).</p>
              </div>
            </div>
        )
    }
}

export default Footer;