let myOptions=[
    {
        label: "8:00-9:00",
        value: "1",
      },
      {
        label: "9:00-10:00",
        value: "2",
      },
      {
        label: "10:00-11:00",
        value: "3",
      },
      {
        label: "11:00-12:00",
        value: "4",
      },
      {
        label: "12:00-13:00",
        value: "5",
      },
      {
        label: "13:00-14:00",
        value: "6",
      },
      {
        label: "14:00-15:00",
        value: "7",
      },
      {
        label: "15:00-16:00",
        value: "8",
      },
      {
        label: "16:00-17:00",
        value: "9",
      },
      {
        label: "17:00-18:00",
        value: "10",
      },
      {
        label: "18:00-19:00",
        value: "11",
      },
];



var instance = new SelectPure(".example", {
    options: myOptions,
    multiple: true // default: false
});


var instance = new SelectPure(".example", {
    placeholder: false
    
});

instance.value();

instance.reset();


var instance = new SelectPure(".example", {
    options: myOptions,
    classNames: {
      select: "select-pure__select",
      dropdownShown: "select-pure__select--opened",
      multiselect: "select-pure__select--multiple",
      label: "select-pure__label",
      placeholder: "select-pure__placeholder",
      dropdown: "select-pure__options",
      option: "select-pure__option",
      autocompleteInput: "select-pure__autocomplete",
      selectedLabel: "select-pure__selected-label",
      selectedOption: "select-pure__option--selected",
      placeholderHidden: "select-pure__placeholder--hidden",
      optionHidden: "select-pure__option--hidden",
    }
});