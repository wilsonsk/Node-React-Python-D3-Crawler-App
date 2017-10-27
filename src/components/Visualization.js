import React from 'react';
import TreeSVGDisplay from './TreeSVGDisplay';

class Visualization extends React.Component {
    constructor(props) {
        super(props);
        
        this.state = {
            crawlJson : ""
        }
        try {
            this.state.crawlJson = JSON.parse(this.props.crawlResults);
        } catch (err) {
            console.warn(err);
        }
    }
    
    componentWillReceiveProps(nextProps) {
        if (this.props.crawlResults !== nextProps.crawlResults) {
            //console.log("next props inside component will receive");
            //console.log(nextProps.crawlResults);
            try {
                this.state.crawlJson = JSON.parse(nextProps.crawlResults);
            } catch (err) {
                console.warn(err);
            }
        }
    }
    
    shouldComponentUpdate(nextProps, nextState) {
        if (this.props.crawlResults !== nextProps.crawlResults) {
            return true;
        }
        return false;
    }
    
    render() {
        if (this.state === "") {
            return(
                <div></div>
            )
        } 
        return(
            <div>
                <TreeSVGDisplay crawlJson = {this.state.crawlJson} />
            </div>
        )
    }
}

export default Visualization;