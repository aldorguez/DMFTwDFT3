  �  #   k820309    9          19.0        /Z�^                                                                                                          
       ../generate_ham.F90 GENERATE_HAM                                                     
                @       �   @                              
       DP          @       �   @                              
       STDOUT MAXLEN                                                                                                                                                                                           �               255                                                                     p          p            p                                     @@                                                       @                                                    @@                              	                                   &                   &                   &                                                                                       
                     @@                                                                 &                   &                   &                                                       @                                                                                                                        &                   &                                                                                                                       &                   &                   &                                                                                                       
                &                   &                                                                                                       
                &                   &                                                                                                       
                &                   &                                                    @@                                                                  &                   &                                           #         @                                                      #GENERATE_HAMR%NUM_NODES    #IO!GENERATE_HAMR%MPIFCMB5    #IO!GENERATE_HAMR%MPIFCMB9    #IO!GENERATE_HAMR%MPIPRIV1    #IO!GENERATE_HAMR%MPIPRIV2    #IO!GENERATE_HAMR%MPIPRIVC                                                                                                                                                                                                         @                                                  #GENERATE_HAMR%MPIFCMB5%MPI_UNWEIGHTED              �   @        �                                                   @                                                  #GENERATE_HAMR%MPIFCMB9%MPI_WEIGHTS_EMPTY              �   @        �                                                   @                                                  #GENERATE_HAMR%MPIPRIV1%MPI_BOTTOM    #GENERATE_HAMR%MPIPRIV1%MPI_IN_PLACE    #GENERATE_HAMR%MPIPRIV1%MPI_STATUS_IGNORE              �   @        �                                               �   @        �                                              �   @        �                                                 p          p            p                                                @                                                  #GENERATE_HAMR%MPIPRIV2%MPI_STATUSES_IGNORE    #GENERATE_HAMR%MPIPRIV2%MPI_ERRCODES_IGNORE              �   @        �                                                  p          p          p            p          p                                            �   @        �                                                 p          p            p                                                @                                                   #GENERATE_HAMR%MPIPRIVC%MPI_ARGVS_NULL !   #GENERATE_HAMR%MPIPRIVC%MPI_ARGV_NULL "   -          �   @        �                 !                                 p          p          p            p          p                                  -          �   @        �                 "                                p          p            p                                     �   )      fn#fn    �   @   J   READ_INPUTS    	  C   J  CONSTANTS    L  N   J  IO    �  p       DP+CONSTANTS    
  s       MAXLEN+IO $   }  �       MP_GRID+READ_INPUTS      @       NR+READ_INPUTS %   Q  @       NUM_WANN+READ_INPUTS !   �  �       HAMR+READ_INPUTS #   M  @       LFORCE+READ_INPUTS "   �  �       DHAMR+READ_INPUTS %   I  @       NUM_KPTS+READ_INPUTS %   �  �       BAND_WIN+READ_INPUTS $   -  �       UMATRIX+READ_INPUTS $   �  �       EIGVALS+READ_INPUTS !   �  �       DEIG+READ_INPUTS %   1  �       KPT_LATT+READ_INPUTS    �  �       TRAN    y	        GENERATE_HAMR .   �
  @     GENERATE_HAMR%NUM_NODES+COMMS 6   8  {   �  IO!GENERATE_HAMR%MPIFCMB5+IO=MPIFCMB5 H   �  H     GENERATE_HAMR%MPIFCMB5%MPI_UNWEIGHTED+IO=MPI_UNWEIGHTED 6   �  ~   �  IO!GENERATE_HAMR%MPIFCMB9+IO=MPIFCMB9 N   y  H     GENERATE_HAMR%MPIFCMB9%MPI_WEIGHTS_EMPTY+IO=MPI_WEIGHTS_EMPTY 6   �  �   �  IO!GENERATE_HAMR%MPIPRIV1+IO=MPIPRIV1 @   �  H     GENERATE_HAMR%MPIPRIV1%MPI_BOTTOM+IO=MPI_BOTTOM D   �  H     GENERATE_HAMR%MPIPRIV1%MPI_IN_PLACE+IO=MPI_IN_PLACE N     �     GENERATE_HAMR%MPIPRIV1%MPI_STATUS_IGNORE+IO=MPI_STATUS_IGNORE 6   �  �   �  IO!GENERATE_HAMR%MPIPRIV2+IO=MPIPRIV2 R   s  �     GENERATE_HAMR%MPIPRIV2%MPI_STATUSES_IGNORE+IO=MPI_STATUSES_IGNORE R   7  �     GENERATE_HAMR%MPIPRIV2%MPI_ERRCODES_IGNORE+IO=MPI_ERRCODES_IGNORE 6   �  �   �  IO!GENERATE_HAMR%MPIPRIVC+IO=MPIPRIVC H   �  �     GENERATE_HAMR%MPIPRIVC%MPI_ARGVS_NULL+IO=MPI_ARGVS_NULL F   D  �     GENERATE_HAMR%MPIPRIVC%MPI_ARGV_NULL+IO=MPI_ARGV_NULL 