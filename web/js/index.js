var app = new Vue({
    el: '#root',
    template: `
      <div>
          <h3>Index component</h3>
          <button @click='onClicked'>Button</button>
      </div>
      `,
    data: {
    },
    mounted () {
    },
    methods: {
      onClicked() {
          console.log("Button clicked.");
          eel.on_button_clicked();
      },
    }
  })
  
  eel.expose(showAlert)
  function showAlert(message) {
      window.alert(message);
  }