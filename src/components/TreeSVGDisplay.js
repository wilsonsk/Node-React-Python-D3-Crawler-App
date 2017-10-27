import React from 'react';
var d3 = require('d3');
var ReactDOM = require('react-dom');

// D3.js code draws inspiration from tree layout examples available from:
// Mike Bostock - Collapsible Tree - https://bl.ocks.org/mbostock/4339083
// Rob Schmuecker - D3.js Drag and Drop, Zoomable, Panning, Collapsible Tree with auto-sizing. - bl.ocks.org/robschmuecker/7880033


// Code for getting the maximum title length of a record in the record list.
function getMaxLabel(records) {
  var maxLen = 0;
  records.forEach( function(record) {
    maxLen = Math.max(record.title === null ? 0 : record.title.length, maxLen);
  });
  return maxLen;
}

// Code for converting a record list to a tree
function buildTree(records) {
  if (records === "") {
      return "";
  }
  
  var resObj = {},
  hash = {};

  records.forEach( function(record) {
    appendRecord(resObj, record, hash);
  });

  return resObj;
}

function appendRecord(obj, record, hash) {
  if (record.parent === null) {
    handleRoot(obj, record, hash);
  } 
  else {
    handleNonRoot(obj, record, hash);
  }
}

function handleRoot(obj, record, hash) {
  obj.url = record.child;
  obj.keyword_found = record.keyword_found;
  obj.title = record.title !== null ? record.title : "No title found";
  obj.children = [];
  // Store key value pair in hash (reference to obj children array)
  hash[obj.url] = obj.children;
}

function handleNonRoot(obj, record, hash) {
  if (typeof hash[record.parent] === undefined) {
    return console.warn("Parent record not found!");
  }

  var childArray = hash[record.parent],
  newNode = {
    url : record.child,
    keyword : record.keyword_found,
    children : []
  };
  newNode.title = record.title !== null ? record.title : "No title found";


  hash[record.child] = newNode.children;

  childArray.push(newNode)
}


// React Component for SVG object. Transfers DOM control to D3 function below.
class TreeSVGDisplay extends React.Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        var mountNode = ReactDOM.findDOMNode(this);
        var treeData = buildTree(this.props.crawlJson);
    
        if (treeData !== "") {
            // Render the tree usng d3 after first component mount
            renderTree(treeData, mountNode, this.props.crawlJson);
        }
    }
    
    shouldComponentUpdate(nextProps, nextState) {
        if (nextProps.crawlJson !== this.props.crawlJson) {    
            var mountNode = ReactDOM.findDOMNode(this);
            var treeData = buildTree(nextProps.crawlJson);
            
            if (treeData !== "") {
                // Remove all child nodes of the current DOM element (svg canvas)
                removeTreeChildren(mountNode);
                
                // Delegate rendering the tree to a d3 function on prop change
                renderTree(treeData, mountNode, nextProps.crawlJson);
            }
        }
        
        // Do not allow react to render the component on prop change
        return false;
    }
    
    render() {
        return(
            <svg></svg>
        );
    }
}

export default TreeSVGDisplay;

function removeTreeChildren(svgDomNode) {
    var svg = d3.select(svgDomNode);
    
    svg.selectAll("*").remove();
}

function renderTree(treeData, svgDomNode, listData) {
    console.log(treeData);
    
    var margin = {top: 20, right: 120, bottom: 20, left: 120},
    width = 960 - margin.right - margin.left,
    height = 800 - margin.top - margin.bottom;

    var i = 0,
    duration = 750,
    root;

    var tree = d3.layout.tree()
        .size([height, width]);

    var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.y, d.x]; });

    var zoomListener = d3.behavior.zoom().scaleExtent([0.1, 3]).on("zoom", zoom);

    var svg = d3.select(svgDomNode)
        .attr("width", width + margin.right + margin.left)
        .attr("height", height + margin.top + margin.bottom)
        .attr("class", "overlay")
        .call(zoomListener);

    var svgGroup = svg.append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var maxLabelLen = getMaxLabel(listData);

    d3.select(window.self.frameElement).style("height", "800px");

    function update(source) {

      // Compute the new tree layout.
      var nodes = tree.nodes(treeData).reverse(),
          links = tree.links(nodes);

      // Set link length dynamically to the length of the longest label.
      nodes.forEach(function(d) { d.y = d.depth * (Math.min(maxLabelLen, 50) * 10); });

      // Update the nodes…
      var node = svgGroup.selectAll("g.node")
          .data(nodes, function(d) { return d.id || (d.id = ++i); });
    
      // Enter any new nodes at the parent's previous position.
      var nodeEnter = node.enter().append("g")
          .attr("class", "node")
          .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
          .on("click", click)
          .on("mouseover", mouseoverC)
          .on("mouseout", mouseoutC);

      nodeEnter.append("circle")
          .attr("r", 1e-6)
          .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });
    
      nodeEnter.append("text")
          .attr("x", function(d) { return d.children || d._children ? -10 : 10; })
          .attr("dy", ".35em")
          .attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })
          .text(function(d) { return d.title; })
          .style("fill-opacity", 1e-6);

      // Transition nodes to their new position.
      var nodeUpdate = node.transition()
          .duration(duration)
          .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });
    
      nodeUpdate.select("circle")
          .attr("r", 4.5)
          .style("fill", function(d) {return d.keyword_found ? "yellow" : "#fff";});
    
      nodeUpdate.select("text")
          .style("fill-opacity", 1);
    
      // Transition exiting nodes to the parent's new position.
      var nodeExit = node.exit().transition()
          .duration(duration)
          .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
          .remove();
    
      nodeExit.select("circle")
          .attr("r", 1e-6);
    
      nodeExit.select("text")
          .style("fill-opacity", 1e-6);

      // Update the links…
      var link = svgGroup.selectAll("path.link")
          .data(links, function(d) { return d.target.id; });
    
      // Enter any new links at the parent's previous position.
      link.enter().insert("path", "g")
          .attr("class", "link")
          .attr("d", function(d) {
            var o = {x: source.x0, y: source.y0};
            return diagonal({source: o, target: o});
          });

      // Transition links to their new position.
      link.transition()
          .duration(duration)
          .attr("d", diagonal);

      // Transition exiting nodes to the parent's new position.
      link.exit().transition()
          .duration(duration)
          .attr("d", function(d) {
            var o = {x: source.x, y: source.y};
            return diagonal({source: o, target: o});
          })
          .remove();

      // Stash the old positions for transition.
      nodes.forEach(function(d) {
        d.x0 = d.x;
        d.y0 = d.y;
      });
    }
    
    // Toggle children on click.
    function click(d) {
      window.open(d.url, '_blank');
    }
    
    // Mouseover and mouseout to display and hide child URL.
    function mouseoverC(d) {
    	  d3.select(this).select("text")
      		.text(function(d) { return d.url });
    }

    function mouseoutC(d) {
    	d3.select(this).select("text")
    		.text(function(d) { return d.title });
    }
    
    // Zoom behavior callback function.
    function zoom() {
    	svgGroup
    		.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
    }
    
    // Center the root node.
    function centerNode(source) {
        var scale = zoomListener.scale();
        var x = -source.y0;
        var y = -source.x0;
        x = x * scale + width / 2;
        y = y * scale + height / 2;
        d3.select('g').transition()
            .duration(duration)
            .attr("transform", "translate(" + x + "," + y + ")scale(" + scale + ")");
        zoomListener.scale(scale);
        zoomListener.translate([x, y]);
    }
    
    // Root initialization code.
    function initialize(root) {
        root.x0 = height / 2;
        root.y0 = 0;
        
        update(root);
        centerNode(root);
    }
    
    initialize(treeData);
}

