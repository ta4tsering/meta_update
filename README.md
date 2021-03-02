# meta_update
  this repo is for to update the meta.yml file of the openpecha opfs
  
#Required Changes 
      
      - when you get the meta.yml file check if the there are "id" and "initial_creation_type" and if there are none then
        create new one and the "id" should be the opf number (P00???)
        
             1. if there are "id" and "initial_creation_type" 
                but if the id : opecha : P00??? then omit the opecha from all the "id"
                in the meta.yml of all the opfs
        
       - If the "initial_creation_type" is ocr then 
            
             1. Get the Image_group and the vol_num from the pagination.yml in the layers of the opfs
                and check the meta.yml file to look for the same image_group and add base_file: vol_num in the dictionary
                
             2. Change the "volume" to "volumnes"
             
         
        
      
