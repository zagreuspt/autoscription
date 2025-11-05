export default {
  async fetch(request, env) {
    const checkString = (str) => {
      const myList = [
        { username: "gianitsi", timeOrder: false },
        { username: "panopoulosparis", timeOrder: true },
        { username: "panopoulouannax", timeOrder: true },
        { username: "troupas1985", timeOrder: true },
        { username: "siapa", timeOrder: true },
        { username: "dimakons", timeOrder: true }
      ];

      const userEntry = myList.find((entry) => entry.username === str);

      if (userEntry) {
        return userEntry.timeOrder;
      } else {
        return null;
      }
    };

    const requestBody = await request.json();
    const name = requestBody.username;
    const checkStringFromRequest = requestBody.check_string;
    const timeOrder = checkString(name);

    const responseData = {
      is_whitelisted: timeOrder !== null,
      check_string: checkStringFromRequest,
      time_order: timeOrder,
    };

    return new Response(JSON.stringify(responseData));
  }
}