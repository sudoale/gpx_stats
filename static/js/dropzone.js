Dropzone.options.performance = {
    init: function() {
      this.on("addedfile", file => {
        console.log("A file has been added");
      });
      this.on("success", (file, response) => {
        alert("File upload successful.");
        window.location.replace(response);
      });
      this.on("error", (file, response) => {
          alert(response);
      });
    }
  };

  Dropzone.options.course = {
    init: function() {
      this.on("addedfile", file => {
        console.log("A file has been added");
      });
      this.on("success", (file, response) => {
        alert("File upload successful.");
        window.location.replace(response);
      });
      this.on("error", (file, response) => {
          alert(response);
      });
    }
  };