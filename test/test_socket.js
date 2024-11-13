const io = require("socket.io-client");

// Connect to the Socket.IO server
const socket = io("http://127.0.0.1:5000");

socket.on("connect", () => {
  console.log("Connected to Socket.IO server");

  // Replace with the actual user ID you want to use
  const userId = "672b1f0102a19d1f20a98de4"; // This is the unique identifier for the user

  // Emit the join_room event and pass the userId in the data object
  socket.emit("join_room", { userId }, (response) => {
    console.log("Join room acknowledgment:", response); // Should confirm the room join
  });
});

socket.on("notification", (data) => {
  console.log("Received notification:", data.message); // This should display the notification message
});

socket.on("disconnect", () => {
  console.log("Disconnected from server");
});

socket.on("connect_error", (error) => {
  console.error("Connection error:", error);
});
